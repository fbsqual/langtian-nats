using System;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using NATS.Client;

class Program
{
    static async Task<int> Main(string[] args)
    {
        var url = args.Length > 0 ? args[0] : "nats://127.0.0.1:4222";
        var count = args.Length > 1 ? int.Parse(args[1]) : 10;

        var opts = ConnectionFactory.GetDefaultOptions();
        opts.Url = url;
        using var c = new ConnectionFactory().CreateConnection(opts);
    var js = c.CreateJetStreamContext();

        for (int i = 0; i < count; i++)
        {
            var msg = new {
                event_id = Guid.NewGuid().ToString(),
                event_type = "battery.telemetry",
                event_timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                schema_version = "1.0",
                source_system = "publisher",
                partition_key = $"device-{i%5}",
                payload = new {
                    device_id = $"device-{i%5}",
                    voltage = 3.7 + (i%10) * 0.01,
                    current = 0.5,
                    temperature = 25.0,
                    state_of_charge = 80.0,
                    cycle_count = 100
                }
            };
            var data = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(msg));
            // For PoC smoke tests use plain publish to ensure messages land on the subject
            // If JetStream is configured with streams for this subject, switch back to js.Publish
            c.Publish("battery.telemetry", data);
            Console.WriteLine($"Published {i+1}");
            await Task.Delay(50);
        }

        return 0;
    }
}
