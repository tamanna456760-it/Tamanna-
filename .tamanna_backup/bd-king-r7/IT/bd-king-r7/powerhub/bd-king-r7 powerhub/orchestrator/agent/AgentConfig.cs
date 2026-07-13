using System;
using System.IO;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

public class AgentConfig
{
    public string RepoPath { get; set; } = ".";
    public string Branch { get; set; } = "powerhub-auto";
    public string Remote { get; set; } = "origin";
    public int IntervalSeconds { get; set; } = 60;
    public bool PushChanges { get; set; } = false;
    public string[] FixCmds { get; set; } = Array.Empty<string>();
    public string[] BuildCmds { get; set; } = Array.Empty<string>();
    public string Ficar { get; set; } = "ficar";
    public string PowerSync { get; set; } = "power_sync";
    public string LockFile { get; set; } = "/var/lock/bd-king-r7.lock";
    public string AgentId { get; set; } = Guid.NewGuid().ToString();
    public string AuthToken { get; set; } = string.Empty;
    public string ServerUrl { get; set; } = string.Empty;

    public static AgentConfig Load(string path)
    {
        try
        {
            if (!File.Exists(path)) return new AgentConfig();
            var text = File.ReadAllText(path);
            var deserializer = new DeserializerBuilder()
                .WithNamingConvention(CamelCaseNamingConvention.Instance)
                .IgnoreUnmatchedProperties()
                .Build();
            var cfg = deserializer.Deserialize<AgentConfig>(text);
            return cfg ?? new AgentConfig();
        }
        catch
        {
            return new AgentConfig();
        }
    }
}
