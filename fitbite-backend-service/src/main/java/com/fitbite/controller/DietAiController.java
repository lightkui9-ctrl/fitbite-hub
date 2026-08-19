package com.fitbite.controller;

import com.fitbite.domain.dto.DietGenerateDTO;
import com.fitbite.service.DietAiService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DataBufferUtils;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * 饮食 AI 控制器 —— 透传 Python AI 服务的 SSE 字节流
 *
 * 项目运行在 Spring MVC (Tomcat Servlet) 上，不是 WebFlux (Netty)。
 * 所以不能用 ServerHttpResponse（WebFlux 接口），要用 HttpServletResponse。
 *
 * 核心做法：拿到 WebClient 的 Flux<DataBuffer>（原始字节），
 * 直接写入 HttpServletResponse 的 OutputStream，blockLast() 阻塞直到流结束。
 */
@Tag(name="饮食管理")
@RestController
@RequestMapping("/api/v1/ai/diet")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DietAiController {

    private final DietAiService dietAiService;

    @Operation(summary = "饮食生成（流式透传 Python AI 服务）")
    @PostMapping(value = "/generate")
    public void generateDiet(@RequestBody DietGenerateDTO dto, HttpServletResponse response) throws java.io.IOException {

        // 1. 设置 SSE 响应头
        response.setContentType(MediaType.TEXT_EVENT_STREAM_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.setHeader("Cache-Control", "no-cache");
        response.setHeader("Connection", "keep-alive");

        // 2. 拿到输出流
        OutputStream out = response.getOutputStream();

        // 3. 订阅 WebClient 的字节流，每个 DataBuffer 直接写入响应
        dietAiService.generateDietStream(dto)
                .doOnNext(buffer -> {
                    try {
                        // 把 DataBuffer 的字节读出来
                        byte[] bytes = new byte[buffer.readableByteCount()];
                        buffer.read(bytes);
                        // 直接写原始字节到 HTTP 响应（保留所有 \n 和 data: 边界）
                        out.write(bytes);
                        out.flush();
                    } catch (java.io.IOException e) {
                        throw new RuntimeException(e);
                    } finally {
                        // 释放 DataBuffer，防止内存泄漏
                        DataBufferUtils.release(buffer);
                    }
                })
                .doOnError(error -> {
                    try {
                        out.write(("data: [ERROR] " + error.getMessage() + "\n\n")
                                .getBytes(StandardCharsets.UTF_8));
                        out.flush();
                    } catch (java.io.IOException ignored) {
                    }
                })
                .blockLast(); // 阻塞当前 Servlet 线程，直到 Flux 完成（保持 HTTP 连接不关闭）
    }

    @Operation(summary = "获取会话历史（用户提问 + AI 回答）")
    @GetMapping("/session/history")
    public String sessionHistory(@RequestParam String sessionId) {
        return dietAiService.getHistory(sessionId);
    }

    @Operation(summary = "清空会话记忆与本地存储")
    @PostMapping("/session/clear")
    public String clearSession(@RequestParam String sessionId) {
        return dietAiService.clearSession(sessionId);
    }
}
