package com.fitbite.domain.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "用户保存/更新请求参数")
public class UserSaveDTO {

    @Schema(description = "用户名", example = "XiaoLiang")
    private String username;

    @Schema(description = "性别 (male/female)", example = "male")
    private String gender;

    @Schema(description = "年龄", example = "25")
    private Integer age;

    @Schema(description = "身高 (cm)", example = "175.0")
    private Double height;

    @Schema(description = "当前体重 (kg)", example = "75.0")
    private Double weight;

    @Schema(description = "目标体重 (kg)", example = "68.0")
    private Double targetWeight;

    @Schema(description = "日常活动量", example = "moderate")
    private String activityLevel;
}