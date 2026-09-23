using Microsoft.AspNetCore.Mvc.RazorPages;

namespace BD_KING_Website.Pages;

//
// ============================================================
// BD-KING-R7 / TAMANNA AI
// Generic Razor Page Model
// Owner: HM INSAN ALI
//
// Purpose:
// - Keeps compatibility with existing pages using:
//       @model GenericModel
// - Provides common project identity information.
// - Provides reusable documentation metadata.
// - Does NOT replace dedicated PageModels such as:
//       IndexModel
//       ProjectModel
//       ProgramSystemModel
//       TamannaAiModel
// ============================================================
//

public class GenericModel : PageModel
{
    // ============================================================
    // PROJECT IDENTITY
    // ============================================================

    public string ApplicationName { get; private set; }
        = "Tamanna AI";

    public string ProjectName { get; private set; }
        = "BD-KING-R7";

    public string WebsiteName { get; private set; }
        = "Powerhub";

    public string OwnerName { get; private set; }
        = "HM INSAN ALI";


    // ============================================================
    // PLATFORM
    // ============================================================

    public string Framework { get; private set; }
        = ".NET 8";

    public string UIFramework { get; private set; }
        = "ASP.NET Core Razor Pages";

    public string Architecture { get; private set; }
        = "Razor Pages";


    // ============================================================
    // DOCUMENTATION STATUS
    // ============================================================

    public string DocumentationStatus { get; private set; }
        = "Available";

    public string SystemStatus { get; private set; }
        = "Documented";


    // ============================================================
    // SYSTEM INFORMATION
    // ============================================================

    public string AutomationLayer { get; private set; }
        = "Tamanna AI";

    public string ProjectDataSource { get; private set; }
        = "Data/projects.json";


    // ============================================================
    // PAGE LOAD
    // ============================================================

    public void OnGet()
    {
        // --------------------------------------------------------
        // Existing behavior is preserved.
        //
        // This model intentionally contains no destructive
        // operations and does not modify project files.
        // --------------------------------------------------------

        DocumentationStatus = "Available";
        SystemStatus = "Documented";
    }
}