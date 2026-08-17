package com.fitbite.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;

@Configuration
public class WebClientConfig {

    @Value("${ai-service.base-url}")
    private String aiServiceBaseUrl;

    @Bean
    public WebClient aiWebClient() {
        // SSE 流式场景：不设 responseTimeout（总超时会截断长流）
        // 仅设连接超时 5s，连接建立后让流自然跑完
        HttpClient httpClient = HttpClient.create()
                .option(io.netty.channel.ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000);

        return WebClient.builder()
                .baseUrl(aiServiceBaseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                // 允许无限缓冲，避免大响应被截断
                .exchangeStrategies(ExchangeStrategies.builder()
                        .codecs(c -> c.defaultCodecs().maxInMemorySize(-1))
                        .build())
                .build();
    }
}