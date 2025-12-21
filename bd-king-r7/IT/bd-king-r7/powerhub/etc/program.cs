using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () =>
{
    var html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>BD-KING-R7 • Sovereign System</title>
        <style>
            body {
                background: #050711;
                color: #f5f5f5;
                font-family: Consolas, monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                border: 1px solid #3f51b5;
                padding: 24px 32px;
                border-radius: 10px;
                box-shadow: 0 0 25px rgba(63, 81, 181, 0.4);
                max-width: 600px;
            }
            h1 {
                margin: 0 0 10px 0;
                font-size: 26px;
                letter-spacing: 1px;
                color: #90caf9;
            }
            h2 {
                margin: 0 0 16px 0;
                font-size: 14px;
                font-weight: normal;
                color: #b0bec5;
            }
            .tag {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 999px;
                border: 1px solid #4caf50;
                font-size: 11px;
                color: #c8e6c9;
                margin-right: 6px;
            }
            .state {
                margin-top: 16px;
                font-size: 13px;
                line-height: 1.6;
            }
            .label {
                color: #b0bec5;
            }
            .value {
                color: #ffffff;
            }
            .domains {
                margin-top: 16px;
                font-size: 12px;
                color: #b0bec5;
            }
            .domains code {
                color: #ffcc80;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="tag">BD-KING-R7</div>
            <div class="tag">VAIRAJ-PROTOCOL</div>
            <h1>Sovereign System Online</h1>
            <h2>Primary node for bd-king-r7.com · .net · .org</h2>

            <div class="state">
                <div><span class="label">Status:</span> <span class="value">ONLINE · LISTENING</span></div>
                <div><span class="label">Engine:</span> <span class="value">Emotion · Power · Drift · Stability · Vairaj</span></div>
                <div><span class="label">Mode:</span> <span class="value">INIT_HANDSHAKE</span></div>
            </div>

            <div class="domains">
                Configure your DNS to point:<br/>
                <code>bd-king-r7.com</code><br/>
                <code>bd-king-r7.net</code><br/>
                <code>bd-king-r7.org</code><br/>
                to this server IP.
            </div>
        </div>
    </body>
    </html>
    """;

    return Results.Content(html, "text/html");
});

app.Run();
