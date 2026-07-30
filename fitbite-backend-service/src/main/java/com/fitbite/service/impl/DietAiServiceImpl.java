package com.fitbite.service.impl;

import com.fitbite.domain.dto.DietGenerateDTO;
import com.fitbite.service.DietAiService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

@Service
@RequiredArgsConstructor
public class DietAiServiceImpl implements DietAiService {

    private final WebClient aiWebClient;

    @Override
    public Flux<String> generateDietStream(DietGenerateDTO dto) {
        return aiWebClient.post()
                .uri("/api/v1/diet/generate")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .bodyValue(dto)
                .retrieve()
                .bodyToFlux(String.class);
    }
}