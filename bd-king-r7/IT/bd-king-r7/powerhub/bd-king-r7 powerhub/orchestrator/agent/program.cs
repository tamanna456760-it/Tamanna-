using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;

await Host.CreateDefaultBuilder(args)
    .ConfigureServices((hostContext, services) =>
    {
        services.AddHostedService<PowerhubAgentWorker>();
    })
    .ConfigureLogging(logging => logging.SetMinimumLevel(LogLevel.Information))
    .RunConsoleAsync();