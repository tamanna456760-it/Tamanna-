using System.Text.Json;
using System.Collections.Generic;
using System.IO;

public record ProjectItem(string Id, string Title, string Short, string Content, string[] Languages, string[] Tags);

public class ProjectStore
{
    private readonly string _dataPath;
    private readonly Dictionary<string, ProjectItem> _items;

    public ProjectStore()
    {
        _dataPath = Path.Combine(Directory.GetCurrentDirectory(), "Data", "projects.json");
        if (!File.Exists(_dataPath))
        {
            _items = new Dictionary<string, ProjectItem>();
            return;
        }
        var json = File.ReadAllText(_dataPath);
        var list = JsonSerializer.Deserialize<List<ProjectItem>>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? new();
        _items = new Dictionary<string, ProjectItem>();
        foreach (var p in list) _items[p.Id] = p;
    }

    public IEnumerable<ProjectItem> GetAll() => _items.Values;
    public ProjectItem? Get(string id) => _items.TryGetValue(id, out var v) ? v : null;
}