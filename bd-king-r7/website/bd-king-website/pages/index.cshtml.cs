using Microsoft.AspNetCore.Mvc.RazorPages;
using System.Collections.Generic;

public class IndexModel : PageModel
{
    private readonly ProjectStore _store;

    // ============================================================
    // BD-KING-R7 / TAMANNA AI
    // Powerhub Website
    // Owner: HM INSAN ALI
    // ============================================================

    public IEnumerable<ProjectItem> Projects { get; private set; }
        = new List<ProjectItem>();

    // ------------------------------------------------------------
    // Project identity
    // ------------------------------------------------------------

    public string ApplicationName { get; private set; }
        = "Tamanna AI";

    public string ProjectName { get; private set; }
        = "BD-KING-R7";

    public string WebsiteName { get; private set; }
        = "Powerhub";

    public string OwnerName { get; private set; }
        = "HM INSAN ALI";

    // ------------------------------------------------------------
    // System status
    // ------------------------------------------------------------

    public string WebsiteStatus { get; private set; }
        = "Online";

    public string ProjectStoreStatus { get; private set; }
        = "Connected";

    public string DockerStatus { get; private set; }
        = "Ready";

    public string TamannaAiStatus { get; private set; }
        = "Integrated";

    // ------------------------------------------------------------
    // Runtime information
    // ------------------------------------------------------------

    public int ProjectCount { get; private set; }

    public string Framework { get; private set; }
        = ".NET 8";

    public string Architecture { get; private set; }
        = "ASP.NET Core Razor Pages";

    // ============================================================
    // Constructor
    // ============================================================

    public IndexModel(ProjectStore store)
    {
        _store = store;
    }

    // ============================================================
    // GET
    // ============================================================

    public void OnGet()
    {
        // Existing ProjectStore workflow is preserved.
        Projects = _store.GetAll();

        // Runtime project count.
        if (Projects is ICollection<ProjectItem> collection)
        {
            ProjectCount = collection.Count;
        }
        else
        {
            ProjectCount = 0;

            foreach (var _ in Projects)
            {
                ProjectCount++;
            }
        }
    }
}