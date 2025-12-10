using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

public class PowerhubAgentWorker : BackgroundService
{
    readonly ILogger<PowerhubAgentWorker> _log;
    AgentConfig _cfg;
    HttpClient _http;

    public PowerhubAgentWorker(ILogger<PowerhubAgentWorker> log)
    {
        _log = log;
        _cfg = AgentConfig.Load("/etc/bdking/agent.yml");
        _http = new HttpClient { Timeout = TimeSpan.FromSeconds(20) };
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _log.LogInformation("Agent starting, interval={interval}s", _cfg.IntervalSeconds);
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await PerformRunAsync();
            }
            catch (Exception ex)
            {
                _log.LogError(ex, "Run failed");
            }
            await Task.Delay(TimeSpan.FromSeconds(_cfg.IntervalSeconds), stoppingToken);
        }
    }

    async Task PerformRunAsync()
    {
        // simple lock by temp file
        var lockFile = _cfg.LockFile ?? "/var/lock/bd-king-r7.lock";
        if (File.Exists(lockFile))
        {
            _log.LogInformation("Lock present; skipping run");
            return;
        }
        File.WriteAllText(lockFile, $"{Process.GetCurrentProcess().Id}");
        try
        {
            // Ensure repo exists
            if (!Directory.Exists(_cfg.RepoPath) || !Directory.Exists(Path.Combine(_cfg.RepoPath, ".git")))
            {
                _log.LogError("Repo path invalid: {p}", _cfg.RepoPath);
                return;
            }

            // git fetch
            RunCmd("git fetch --all --prune", _cfg.RepoPath);

            // checkout/create branch
            if (RunCmdIgnoreError($"git rev-parse --verify {_cfg.Branch}", _cfg.RepoPath) == 0)
                RunCmd($"git checkout {_cfg.Branch}", _cfg.RepoPath);
            else
            {
                var rc = RunCmdIgnoreError($"git ls-remote --exit-code {_cfg.Remote} main", _cfg.RepoPath);
                if (rc == 0) RunCmd($"git checkout -b {_cfg.Branch} {_cfg.Remote}/main", _cfg.RepoPath);
                else RunCmd($"git checkout -b {_cfg.Branch}", _cfg.RepoPath);
            }

            // pull
            RunCmd($"git pull --rebase {_cfg.Remote} {_cfg.Branch}", _cfg.RepoPath);

            // run fixers
            var fixerOut = new System.Collections.Generic.List<object>();
            foreach (var cmd in _cfg.FixCmds ?? Array.Empty<string>())
            {
                var (rc, outp) = RunCmdCapture(cmd, _cfg.RepoPath);
                fixerOut.Add(new { cmd, rc, outp });
            }

            // git add all (after fixers)
            RunCmd("git add -A", _cfg.RepoPath);

            // build/test
            bool buildOk = true;
            var buildOut = new System.Collections.Generic.List<object>();
            foreach (var cmd in _cfg.BuildCmds ?? Array.Empty<string>())
            {
                var (rc, outp) = RunCmdCapture(cmd, _cfg.RepoPath);
                buildOut.Add(new { cmd, rc, outp });
                if (rc != 0) { buildOk = false; break; }
            }

            // update marker files
            var uid = Guid.NewGuid().ToString();
            File.WriteAllText(Path.Combine(_cfg.RepoPath, _cfg.Ficar ?? "ficar"), $"Updated at: {DateTime.UtcNow:O}\nUUID: {uid}\n");
            File.WriteAllText(Path.Combine(_cfg.RepoPath, _cfg.PowerSync ?? "power_sync"), $"Last run: {DateTime.UtcNow:O} BUILD_OK={buildOk}\n");
            RunCmd($"git add \"{_cfg.Ficar}\" \"{_cfg.PowerSync}\" || true", _cfg.RepoPath);

            // check for changes
            var (statusRc, statusOut) = RunCmdCapture("git status --porcelain", _cfg.RepoPath);
            bool hasChanges = !string.IsNullOrWhiteSpace(statusOut);

            bool committed = false;
            string commitSha = null;
            if (hasChanges && buildOk)
            {
                RunCmd($"git commit -m \"Automated sync/fix/build {DateTime.UtcNow:O}\"", _cfg.RepoPath);
                committed = true;
                commitSha = RunCmdCaptureRaw("git rev-parse --short HEAD", _cfg.RepoPath).Trim();
                if (_cfg.PushChanges) RunCmd($"git push -u {_cfg.Remote} {_cfg.Branch}", _cfg.RepoPath);
            }
            else if (hasChanges && !buildOk)
            {
                // unstage to allow manual review
                RunCmd("git reset --mixed", _cfg.RepoPath);
            }

            // post to orchestrator
            if (!string.IsNullOrWhiteSpace(_cfg.ServerUrl))
            {
                var payload = new
                {
                    agentId = _cfg.AgentId,
                    branch = _cfg.Branch,
                    buildOk,
                    committed,
                    commitSha,
                    fixerOut,
                    buildOut,
                    hasChanges,
                    repoPath = _cfg.RepoPath
                };
                var json = JsonSerializer.Serialize(payload);
                var req = new HttpRequestMessage(HttpMethod.Post, _cfg.ServerUrl.TrimEnd('/') + "/api/report");
                req.Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
                if (!string.IsNullOrWhiteSpace(_cfg.AuthToken)) req.Headers.Add("Authorization", $"Bearer {_cfg.AuthToken}");
                var res = await _http.SendAsync(req);
                _log.LogInformation("Report posted, status {s}", res.StatusCode);
            }
        }
        finally
        {
            if (File.Exists(lockFile)) File.Delete(lockFile);
        }
    }

    int RunCmd(string cmd, string cwd)
    {
        var psi = new ProcessStartInfo("/bin/bash", $"-lc \"{cmd}\"")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            WorkingDirectory = cwd,
            UseShellExecute = false
        };
        var p = Process.Start(psi);
        p.WaitForExit();
        var outp = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
        _log.LogDebug("CMD: {cmd} => {rc}\n{out}", cmd, p.ExitCode, outp);
        return p.ExitCode;
    }

    int RunCmdIgnoreError(string cmd, string cwd) { try { return RunCmd(cmd, cwd); } catch { return -1; } }

    (int rc, string outp) RunCmdCapture(string cmd, string cwd)
    {
        var psi = new ProcessStartInfo("/bin/bash", $"-lc \"{cmd}\"")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            WorkingDirectory = cwd,
            UseShellExecute = false
        };
        var p = Process.Start(psi);
        var outp = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
        p.WaitForExit();
        _log.LogDebug("CMD: {cmd} => {rc}\n{out}", cmd, p.ExitCode, outp);
        return (p.ExitCode, outp);
    }

    string RunCmdCaptureRaw(string cmd, string cwd)
    {
        var (rc, outp) = RunCmdCapture(cmd, cwd); return outp.Trim();
    }
}