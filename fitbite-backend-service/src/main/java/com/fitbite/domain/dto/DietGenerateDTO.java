package com.fitbite.domain.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import java.util.List;

@Data
@Schema(description = "减脂餐生成请求参数")
public class DietGenerateDTO {

    @Schema(description = "性别", example = "male")
    private String gender;

    @Schema(description = "年龄", example = "23")
    private Integer age;

    @Schema(description = "身高 (cm)", example = "186.0")
    private Double height;

    @Schema(description = "体重 (kg)", example = "88.0")
    private Double weight;

    @Schema(description = "日常活动量 (sedentary/light/moderate/active/very_active)", example = "moderate")
    private String activityLevel;

    @Schema(description = "目标减重 (kg)", example = "5.0")
    private Double targetWeightLoss;

    @Schema(description = "现有食材列表", example = "[\"鸡胸肉\", \"西兰花\", \"鸡蛋\"]")
    private List<String> availableIngredients;

    @Schema(description = "忌口/过敏源", example = "[]")
    private List<String> dietaryRestrictions;

    @Schema(description = "多轮追问的自然语言消息。传入时直接使用并复用会话历史", example = "把早餐换成更低脂的方案")
    private String message;

    @Schema(description = "会话 ID，用于多轮记忆隔离。前端每次会话生成唯一值", example = "sess-abc123")
    private String sessionId;
}