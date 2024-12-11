import type { Server } from 'http';
import { app, net } from 'electron';
import type { Logger } from './RemoteLogger';

const PROXY_HOSTS = [
  { host: 'www.pathofexile.com', official: true },
  { host: 'ru.pathofexile.com', official: true },
  { host: 'pathofexile.tw', official: true },
  { host: 'poe.game.daum.net', official: true },
  { host: 'poe.ninja', official: false },
  { host: 'www.poeprices.info', official: false },
];

export class HttpProxy {
  constructor (
    server: Server,
    logger: Logger
  ) {
    server.addListener('request', (req, res) => {
      if (!req.url?.startsWith('/proxy/')) return;

      const host = req.url.split('/', 3)[2];
      logger.write(`Incoming request to proxy: ${req.url}`);

      const official = PROXY_HOSTS.find(entry => entry.host === host)?.official;
      if (official === undefined) {
        logger.write(`Host not officially supported: ${host}`);
        return req.destroy(); // Log rejection on unsupported host
      }

      // Log headers before modifying them
      for (const key in req.headers) {
        if (key.startsWith('sec-') || key === 'host' || key === 'origin' || key === 'content-length') {
          delete req.headers[key];
        }
      }

      const url = req.url.slice('/proxy/'.length);
      logger.write(`Incoming request headers: ${JSON.stringify(req.headers)}`);
      logger.write(`Proxying ${req.method} request to https://${url}`);
      logger.write(`Fallback user-agent: ${app.userAgentFallback}`);

      // Collect POST body data if applicable
      let bodyData = '';
      req.on('data', (chunk) => {
        bodyData += chunk.toString(); // Accumulate incoming data
      });

      req.on('end', () => {
        if (req.method === 'POST') {
          logger.write(`Incoming POST body: ${bodyData}`); // Log the complete POST body
        }
        
        // Now pipe the request to the proxy
        const proxyReq = net.request({
          url: 'https://' + url,
          method: req.method,
          headers: {
            ...req.headers,
            'user-agent': app.userAgentFallback
          },
          useSessionCookies: true
        });

        proxyReq.addListener('response', (proxyRes) => {
          const resHeaders = { ...proxyRes.headers };
          logger.write(`Proxy response status: ${proxyRes.statusCode}, status message: ${proxyRes.statusMessage}`);
          logger.write(`Proxy response headers: ${JSON.stringify(resHeaders)}`);

          let responseBody = '';
          proxyRes.on('data', (chunk) => {
            responseBody += chunk.toString(); // Accumulate response body
          });

          proxyRes.on('end', () => {
            logger.write(`Proxy response body: ${responseBody}`); // Log the complete response body
            delete resHeaders['content-encoding'];
            res.writeHead(proxyRes.statusCode, proxyRes.statusMessage, resHeaders);
            res.end(responseBody); // Send the body back to the original request
          });
          
        });

        proxyReq.addListener('error', (err) => {
          logger.write(`Error during proxy request: ${err.message} (${host}); is this a network error?`);
          res.writeHead(502, 'Bad Gateway');
          res.end(`Proxy error: ${err.message}`);
        });

        // Write the request body to the proxy request if it exists
        if (bodyData) {
          proxyReq.write(bodyData);
        }
        
        req.pipe(proxyReq as unknown as NodeJS.WritableStream);
      });
    });
  }
}