package com.fitbite.controller;

import com.fitbite.domain.dto.DietGenerateDTO;
import com.fitbite.service.DietAiService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@Tag(name="饮食管理")
@RestController
@RequestMapping("/api/v1/ai/diet")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // 开发阶段跨域放行
public class DietAiController {

    private final DietAiService dietAiService;

    @Operation(summary = "饮食生成")
    @PostMapping(value = "/generate", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> generateDiet(@RequestBody DietGenerateDTO dto) {
        return dietAiService.generateDietStream(dto);
    }
}