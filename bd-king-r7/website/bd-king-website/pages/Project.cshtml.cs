using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace BD_KING_Website.Pages;

/// <summary>
/// Supplies project details to the existing project Razor page.
/// </summary>
public sealed class ProjectModel : PageModel
{
    private readonly ProjectStore _store;

    public ProjectModel(ProjectStore store)
    {
        _store = store;
    }

    public ProjectItem? Item { get; private set; }
    public bool ProjectFound => Item is not null;
    public string StatusMessage { get; private set; } = "Project was not found.";
    public string Status { get; private set; } = "Not found";

    public int LanguageCount => Languages.Count;
    public int TagCount => Tags.Count;
    public int ContentLength => Item?.Content?.Length ?? 0;

    public IReadOnlyList<string> Languages { get; private set; } = Array.Empty<string>();
    public IReadOnlyList<string> Tags { get; private set; } = Array.Empty<string>();

    public string ApplicationName { get; } = "Tamanna AI";
    public string ProjectName { get; } = "BD-KING-R7";
    public string Framework { get; } = ".NET 8";
    public string OwnerName { get; } = "HM INSAN ALI";

    public void OnGet(string? id)
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            StatusMessage = "No project identifier was supplied.";
            return;
        }

        Item = _store.Get(id.Trim());
        if (Item is null)
        {
            StatusMessage = "The requested project does not exist.";
            return;
        }

        Status = "Available";
        StatusMessage = "Project details loaded.";
        Languages = (Item.Languages ?? Array.Empty<string>())
            .Where(value => !string.IsNullOrWhiteSpace(value))
            .ToArray();
        Tags = (Item.Tags ?? Array.Empty<string>())
            .Where(value => !string.IsNullOrWhiteSpace(value))
            .ToArray();
    }
}
