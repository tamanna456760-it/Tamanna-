using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using System.Text.Json;
using Microsoft.AspNetCore.Http;
using System;
using System.Linq;
using System.Threading.Tasks;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetValue<string>("Database:ConnectionString") ?? "Data Source=reports.db"));
builder.Services.AddEndpointsApiExplorer();

var app = builder.Build();

app.MapPost("/api/report", async (HttpRequest request, AppDbContext db, IConfiguration cfg) =>
{
    // Simple token auth using header Authorization: Bearer <token>
    var expected = cfg.GetValue<string>("Orchestrator:Token") ?? "change-me";
    if (!request.Headers.TryGetValue("Authorization", out var auth) || !auth.ToString().StartsWith("Bearer "))
        return Results.Unauthorized();
    var token = auth.ToString().Substring("Bearer ".Length).Trim();
    if (token != expected) return Results.StatusCode(403);

    ReportPayload payload;
    try
    {
        payload = await JsonSerializer.DeserializeAsync<ReportPayload>(request.Body);
    }
    catch
    {
        return Results.BadRequest(new { error = "invalid json" });
    }
    var r = new Report
    {
        AgentId = payload.AgentId,
        Timestamp = DateTime.UtcNow,
        Branch = payload.Branch,
        BuildOk = payload.BuildOk ? "true" : "false",
        Committed = payload.Committed ? "true" : "false",
        CommitSha = payload.CommitSha ?? "",
        PayloadJson = JsonSerializer.Serialize(payload)
    };
    db.Reports.Add(r);
    await db.SaveChangesAsync();
    return Results.Created($"/api/report/{r.Id}", new { status = "ok" });
});

app.MapGet("/", async (AppDbContext db) =>
{
    var rows = db.Reports.OrderByDescending(r => r.Id).Take(200).ToArray();
    var html = "<html><head><title>bd-king-r7 Orchestrator</title></head><body>";
    html += "<h1>bd-king-r7 Orchestrator - Recent Reports</h1>";
    html += "<table border=1 cellpadding=6><tr><th>ID</th><th>Agent</th><th>Time</th><th>Branch</th><th>Build</th><th>Committed</th><th>Commit</th></tr>";
    foreach (var r in rows)
    {
        html += $"<tr><td>{r.Id}</td><td>{r.AgentId}</td><td>{r.Timestamp:O}</td><td>{r.Branch}</td><td>{r.BuildOk}</td><td>{r.Committed}</td><td>{r.CommitSha}</td></tr>";
    }
    html += "</table></body></html>";
    return Results.Content(html, "text/html");
});

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}

app.Run();


// Small DTO for incoming payload
public class ReportPayload
{
    public string AgentId { get; set; }
    public string Branch { get; set; }
    public bool BuildOk { get; set; }
    public bool Committed { get; set; }
    public string CommitSha { get; set; }
    public object FixerOut { get; set; }
    public object BuildOut { get; set; }
    public bool HasChanges { get; set; }
    public string RepoPath { get; set; }
}