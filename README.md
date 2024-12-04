<br/><br/><p align="center">
  <img src="https://lirp.cdn-website.com/c10be9aa/dms3rep/multi/opt/Optiorix+full+transparant+background+-+blue-c6d680b3-1920w.png" width="250"/>
</p><br/><br/>

# Introduction to OptiPick Webhooks

Webhooks allow services to notify each other of events. At their core, they are simply `POST` requests sent to a pre-determined endpoint. You can define your own endpoints in our web application and configure different endpoints for various combinations of *event types*. 

OptiPick supports the following event types:

- **`route.optimized`**: Triggered when a request to our routing API completes for **any** of your operational warehouses.
- **`cluster.optimized`**: Triggered when a request to our clustering API completes for **any** of your operational warehouses.
- **`route.optimized.{warehouse name}.{your user id}`**: Triggered when a request to our routing API completes for a specific `{warehouse name}`.
- **`cluster.optimized.{warehouse name}.{your user id}`**: Triggered when a request to our clustering API completes for a specific `{warehouse name}`.

Once subscribed to one or more types, your endpoint receives small messages whenever the chosen events occur. These messages include the `ID` of the completed request, which can be used to fetch further details from our REST API.

This minimal Flask application demonstrates how your webhook endpoint should process events. For incoming `cluster.optimized.{warehouse name}.{your user id}` events, the example verifies the payload using request headers and your endpoint's ***secret***. Additionally, it showcases how to use our REST API to retrieve optimization details.

## Setting Up Webhooks 

To set up webhooks, navigate to the ***Webhook Dashboard*** under ***Settings*** in the [web application](https://optipick.optioryx.com/settings).

![](/img/webhooks.png)

On the webhooks dashboard, you'll see the "Endpoints" page.

![](/img/new_endpoint.png)

Click the "Add Endpoint" button to create a new endpoint. For production, you should deploy your endpoint to a domain or IP accessible by our [webhook workers](https://docs.optioryx.com/optipick-webhooks). For debugging, you can use the [Svix CLI](https://github.com/svix/svix-cli?tab=readme-ov-file#installation) to forward a temporary "playground" endpoint to your localhost. 

After installing the CLI, start your Flask application with:

```bash
python main.py
``` 

Assuming the application runs at `http://127.0.0.1:5000` (check the output of the command above) and your webhook endpoint is `/webhook`, you can forward requests locally using:

```bash
svix listen http://127.0.0.1:5000/webhook
```

The CLI output provides a webhook URL that redirects callbacks to your local machine.

![Forwarding Example](/img/svix_forward.png)

Enter this relay URL in the "Add Endpoint" screen, then select the event types you wish to listen for (e.g., `cluster.optimized` for the "Example" warehouse: `cluster.optimized.Example.673f48095739843f4de65ec9`).

![Create Endpoint](/img/svix_endpoint_create.png)

After creating the endpoint, reveal the signing secret to verify calls from our servers. Set the variable `secret` in `main.py` to match this value (and restart the Flask app after any changes).

![Signing Secret](/img/signing_secret.png)

## Setting Up the REST API

Your app is now ready to receive events containing unique optimization IDs. To fetch a completed optimization's outcome, use this ID and a secret API key to query the [OptiPick API](https://docs.optioryx.com).

To create an API key:

1. Go to the **Settings** page in the [web application](https://optipick.optioryx.com/settings).
2. Click on "API Keys."
3. Generate a new API key.

Set the variable `api_key` in `main.py` to your API key (restart the Flask app after any changes).

![](/img/api-key-in-settings.png)
![](/img/new-api-key.png)

## Trying It Out

Once `main.py` contains all the necessary tokens, your app is ready to receive events! Submit the default clustering request for the "Example" warehouse from our [API docs](https://docs.optioryx.com), ensuring your API key is filled in and `synchronous` is set to `false`. After a few seconds, the optimization results should appear in your Flask console.

![](/img/docs-page.png)
![](/img/console-input.png)

The webhook dashboard for your endpoint also logs incoming requests. You can replay these manually ([requests are also retried automatically at various intervals](https://docs.optioryx.com/optipick-webhooks)). To test this, introduce an intentional fatal error in `main.py`, start an optimization, fix the error, and replay the event via the dashboard. The system marks an event as handled only if your endpoint responds with a `20X` status code.

![](/img/replay.png)