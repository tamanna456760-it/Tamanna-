using Microsoft.AspNetCore.Mvc.RazorPages;
using System.Collections.Generic;

public class IndexModel : PageModel
{
    private readonly ProjectStore _store;
    public IEnumerable<ProjectItem> Projects { get; private set; } = new List<ProjectItem>();

    public IndexModel(ProjectStore store)
    {
        _store = store;
    }

    public void OnGet()
    {
        Projects = _store.GetAll();
    }
}