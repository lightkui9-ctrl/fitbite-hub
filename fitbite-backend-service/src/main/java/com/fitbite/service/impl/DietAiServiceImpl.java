package com.fitbite.service.impl;

import com.fitbite.domain.dto.DietGenerateDTO;
import com.fitbite.service.DietAiService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

/**
 * 饮食 AI 服务实现 —— 透传 Python FastAPI 的 SSE 字节流
 *
 * 关键设计：用 DataBuffer 透传原始字节流，绝不用 String.class
 *
 * 原因：bodyToFlux(String.class) 会触发 SSE decoder，把多行 data: 合并成
 * 单个 String（不用 \n 分隔），导致换行全丢。
 *
 * 用 DataBuffer.class 拿到的是原始字节块，不做任何解析。
 */
@Service
@RequiredArgsConstructor
public class DietAiServiceImpl implements DietAiService {

    private final WebClient aiWebClient;

    @Override
    public Flux<DataBuffer> generateDietStream(DietGenerateDTO dto) {
        return aiWebClient.post()
                .uri("/api/v1/diet/generate")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(dto)
                .retrieve()
                .bodyToFlux(DataBuffer.class);  // 原始字节，不做 SSE 解析
    }

    @Override
    public String getHistory(String sessionId) {
        return aiWebClient.get()
                .uri("/api/v1/diet/session/history?session_id={sid}", sessionId)
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }

    @Override
    public String clearSession(String sessionId) {
        return aiWebClient.post()
                .uri("/api/v1/diet/session/clear?session_id={sid}", sessionId)
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }
}
