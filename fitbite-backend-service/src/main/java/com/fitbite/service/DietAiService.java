package com.fitbite.service;

import com.fitbite.domain.dto.DietGenerateDTO;
import org.springframework.core.io.buffer.DataBuffer;
import reactor.core.publisher.Flux;

/**
 * 流式透传调用 Python AI 微服务生成减脂餐
 *
 * 返回类型改为 Flux<DataBuffer>，透传原始字节流（避免多行 SSE data 合并）
 */
public interface DietAiService {
    Flux<DataBuffer> generateDietStream(DietGenerateDTO dto);

    /** 获取会话历史（用户提问 + AI 回答），JSON 字符串透传自 Python */
    String getHistory(String sessionId);

    /** 清空会话记忆与本地存储，JSON 字符串透传自 Python */
    String clearSession(String sessionId);
}
