// Minimal .NET Core UDP collector (console app scaffold)
// Listens on UDP for incoming Envelope JSON (or protobuf bytes) and publishes to NATS JetStream

// Notes:
// - Requires NuGet: NATS.Client
// - For production, wrap as a Windows Service (Worker Service template)

// ...existing code...

using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using NATS.Client;
using System.Text.Json;

class UdpCollector
{
    static async Task Main(string[] args)
    {
        int port = 9000;
        if (args.Length > 0) int.TryParse(args[0], out port);

        Console.WriteLine($"Starting UDP Collector on port {port}");
        UdpClient udp = new UdpClient(port);

        // NATS connection
        Options opts = ConnectionFactory.GetDefaultOptions();
        opts.Url = "nats://127.0.0.1:4222"; // change as needed

        using (IConnection c = new ConnectionFactory().CreateConnection(opts))
        {
            // Ensure JetStream stream exists in your NATS server; this code assumes a subject 'battery.telemetry'
            var js = c.CreateJetStreamContext();

            while (true)
            {
                var result = await udp.ReceiveAsync();
                var data = result.Buffer;

                // Try parse as JSON first
                string s = null;
                try
                {
                    s = Encoding.UTF8.GetString(data);
                    using var doc = JsonDocument.Parse(s);
                    // Optionally validate envelope schema here
                    // Publish raw bytes to JetStream
                    js.Publish("battery.telemetry", data);
                    Console.WriteLine($"Published JSON envelope, len={data.Length}");
                }
                catch (Exception)
                {
                    // If not JSON, publish as-is (assume protobuf envelope bytes)
                    try
                    {
                        js.Publish("battery.telemetry", data);
                        Console.WriteLine($"Published raw envelope, len={data.Length}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Publish failed: {ex.Message}");
                    }
                }
            }
        }
    }
}
