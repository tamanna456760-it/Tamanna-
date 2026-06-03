using Microsoft.EntityFrameworkCore;
using System;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> opts) : base(opts) { }
    public DbSet<Report> Reports { get; set; }
}

public class Report
{
    public int Id { get; set; }
    public string AgentId { get; set; }
    public DateTime Timestamp { get; set; }
    public string Branch { get; set; }
    public string BuildOk { get; set; }
    public string Committed { get; set; }
    public string CommitSha { get; set; }
    public string PayloadJson { get; set; }
}