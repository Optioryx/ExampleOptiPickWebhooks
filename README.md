<br/><br/><p align="center">
  <img src="https://lirp.cdn-website.com/c10be9aa/dms3rep/multi/opt/Optiorix+full+transparant+background+-+blue-c6d680b3-1920w.png" width="250"/>
</p><br/><br/>

# Introduction to OptiPick Webhooks
Webhooks are how services notify each other of events. At their core they are just a  `POST`  request to a pre-determined endpoint. The endpoint can be whatever you want, and you can just add your own in our web application. You can configure different endpoints for different combinations *event types*. OptiPick provides the following event types
- `route.optimized`: Triggered when a request to our routing API completes for **any** of your operational warehouses
- `cluster.optimized`: Triggered when a request to our clustering API completes for **any** of your operational warehouses
- `route.optimized.{warehouse name}.{your user id}`: Triggered when a request to our routing API completes for `{warehouse name}`
- `cluster.optimized.{warehouse name}.{your user id}`: Triggered when a request to our clustering API completes for `{warehouse name}`

Once subscribed to one or more types, your endpoint receives small messages whenever the chosen events occur. This message contains the `ID` of the completed request, which you can use to fetch further details from our REST API.

This minimal Flask application serves as an illustration of what your webhook endpoint has to do. For incoming `cluster.optimized.{warehouse name}.{your user id}` events, this endpoint verifies the payload using the request headers and your endpoint ***secret***. We also illustrate how to use our REST API to gather the optimization's details.

## Setting up webhooks 
To set up webhooks, you will need to navigate to the ***Webhook Dashboard***, which is accessible through ***Settings*** in the [webapp](https://optipick.optioryx.com/settings).

![](/img/webhooks.png)

In the webhooks dashboard, you will be greeted with the endpoints page.

![](/img/new_endpoint.png)

You can click the "Add Endpoint" button to add your new endpoint. In production, you will deploy your endpoint to a domain or IP that is accessible [by our webhook workers](https://docs.optioryx.com/optipick-webhooks), but for debugging, you can use the [Svix CLI](https://github.com/svix/svix-cli?tab=readme-ov-file#installation) to forward a "playground" endpoint to your localhost. After installing the CLI, we start our Flask application:
```
python main.py
``` 
Assuming our application is running on `http://127.0.0.1:5000` (should be visible in the output of the above command) and your webhook endpoint lives at `/webhook` (which is the case in this example), we can run 
```
svix listen http://127.0.0.1:5000/webhook
```
From the output of this command, we can find a webhook URL that will redirect any callbacks to our local machine.

![Forward](/img/svix_forward.png)

In the "Add Endpoint" screen that we navigated to earlier, we can now fill in the relay URL and select the event types that we will be listening to (in this case the `cluster.optimized` endpoint for warehouse "Example", `cluster.optimized.Example.673f48095739843f4de65ec9`).

![Forward](/img/svix_endpoint_create.png)

After creating the endpoint, we can reveal the signing secret used to verify that this call actually originates from our servers. The variable `secret` in `main.py` should be equal to this text (don't forget to restart your Flask app after any changes).

![Forward](/img/signing_secret.png)

## Setting up the REST API
Your app is now ready to receive events that contain a unique optimization IDs. To reveal a finished optimization's outcome, we need to use this ID and a secret API key to query the [OptiPick API](https://docs.optioryx.com).

To create an API key, you will again need to navigate to the **Settings** page in the [webapp](https://optipick.optioryx.com/settings) and look for the "API Keys" button. The variable `api_key` in `main.py` should be set to your API key (don't forget to restart your Flask app after any changes).

![](/img/api-key-in-settings.png)
![](/img/new-api-key.png)

## Trying it out
Once `main.py` contains all necessary tokens, you're ready to receive events! Try to submit the default example clustering request for the "Example" warehouse from our [API docs](https://docs.optioryx.com) page, with your API key filled in and `synchronous` set to false. After a few seconds, you should see the optimizion's results printed in your Flask console. 
![](/img/docs-page.png)

On the webhook dashboard page for your endpoint, you should also see a log of requests. This allows for manual replay ([although requests are also retried automatically at various time intervals](https://docs.optioryx.com/optipick-webhooks)). To test this out, you could try to intentionally add a fatal error to your endpoint in `main.py`, start an optimization, fix the error and click replay in the dashboard. The event system will only mark an event as handled if your endpoint responds with a `20X` response code.

![](/img/replay.png)
