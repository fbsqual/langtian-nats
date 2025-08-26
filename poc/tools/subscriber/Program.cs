using System;
using System.Text;
using NATS.Client;

class Program {
    static int Main(string[] args) {
        var url = args.Length > 0 ? args[0] : "nats://127.0.0.1:4222";
        var count = args.Length > 1 ? int.Parse(args[1]) : 10;
        var opts = ConnectionFactory.GetDefaultOptions();
        opts.Url = url;
        using var c = new ConnectionFactory().CreateConnection(opts);
        using var s = c.SubscribeSync("battery.telemetry");
        Console.WriteLine("Subscribed to battery.telemetry, waiting for messages...");
        for (int i = 0; i < count; i++) {
            var msg = s.NextMessage(5000);
            if (msg == null) { Console.WriteLine("Timeout"); break; }
            var text = Encoding.UTF8.GetString(msg.Data);
            Console.WriteLine($"[{i+1}] {text}");
        }
        return 0;
    }
}
