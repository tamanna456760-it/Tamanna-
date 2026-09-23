using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;


// ============================================================
// BD-KING-R7 / TAMANNA AI
// Powerhub Website
//
// Owner: HM INSAN ALI
// Framework: ASP.NET Core 8
// UI: Razor Pages
// ============================================================


var builder = WebApplication.CreateBuilder(args);


// ============================================================
// APPLICATION INFORMATION
// ============================================================

builder.Configuration.AddEnvironmentVariables();


// ============================================================
// SERVICES
// ============================================================

// Razor Pages
builder.Services.AddRazorPages();


// Project data store
builder.Services.AddSingleton<ProjectStore>();


// HTTP Context
builder.Services.AddHttpContextAccessor();


// Health checks
builder.Services.AddHealthChecks();


// ============================================================
// BUILD APPLICATION
// ============================================================

var app = builder.Build();


// ============================================================
// ERROR HANDLING
// ============================================================

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");

    app.UseHsts();
}


// ============================================================
// SECURITY HEADERS
// ============================================================

app.Use(async (context, next) =>
{
    context.Response.Headers["X-Content-Type-Options"] =
        "nosniff";

    context.Response.Headers["X-Frame-Options"] =
        "SAMEORIGIN";

    context.Response.Headers["Referrer-Policy"] =
        "strict-origin-when-cross-origin";

    context.Response.Headers["Permissions-Policy"] =
        "camera=(), microphone=(), geolocation=()";

    await next();
});


// ============================================================
// STATIC FILES
// ============================================================

app.UseStaticFiles();


// ============================================================
// ROUTING
// ============================================================

app.UseRouting();


// ============================================================
// RAZOR PAGES
// ============================================================

app.MapRazorPages();


// ============================================================
// HEALTH ENDPOINT
// ============================================================

app.MapHealthChecks("/health");


// ============================================================
// SYSTEM INFORMATION
// ============================================================

app.MapGet("/api/system/info", () =>
{
    return Results.Ok(new
    {
        system = "Tamanna AI",
        project = "BD-KING-R7",
        website = "Powerhub",
        framework = ".NET 8",
        status = "online"
    });
});


// ============================================================
// SIMPLE STATUS ENDPOINT
// ============================================================

app.MapGet("/api/system/status", () =>
{
    return Results.Ok(new
    {
        website = "online",
        razor_pages = "online",
        project_store = "registered",
        health = "available"
    });
});


// ============================================================
// APPLICATION START
// ============================================================

app.Run();


// ============================================================
// PROGRAM CLASS
//
// Required for future integration / WebApplicationFactory
// and automated tests.
// ============================================================

public partial class Program
{
}