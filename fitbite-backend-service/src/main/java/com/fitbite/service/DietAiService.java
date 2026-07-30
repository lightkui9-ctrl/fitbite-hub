package com.fitbite.service;

import com.fitbite.domain.dto.DietGenerateDTO;
import reactor.core.publisher.Flux;

public interface DietAiService {
    /**
     * 流式透传调用 Python AI 微服务生成减脂餐
     */
    Flux<String> generateDietStream(DietGenerateDTO dto);
}