using Microsoft.AspNetCore.Mvc.RazorPages;

namespace BD_KING_Website.Pages;

/// <summary>
/// Supplies stable application and component status information
/// to the Tamanna AI Razor page.
/// </summary>
public sealed class TamannaAiModel : PageModel
{
    public string SystemStatus { get; private set; } = "Configured";
    public string ProjectName { get; } = "BD-KING-R7";
    public int ComponentCount { get; } = 4;
    public string Framework { get; } = ".NET 8";
    public string AgentStatus { get; private set; } = "Configured";
    public string OrchestratorStatus { get; private set; } = "Configured";
    public string AutoFixStatus { get; private set; } = "Configured";
    public string ReportingStatus { get; private set; } = "Configured";
    public string ApplicationName { get; } = "Tamanna AI";
    public string WebsiteName { get; } = "Powerhub";
    public string Architecture { get; } = "ASP.NET Core Razor Pages";
    public string OwnerName { get; } = "HM INSAN ALI";

    public void OnGet()
    {
        // These values describe configured components, not live health checks.
        SystemStatus = "Configured";
    }
}
