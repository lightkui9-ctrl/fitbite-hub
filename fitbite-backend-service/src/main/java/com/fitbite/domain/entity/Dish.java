package com.fitbite.domain.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.util.List;

@Data
@TableName("sys_dish")
public class Dish {
    @TableId
    private Long id;
    private String name;
    private Integer calories;
    private Double protein;
    private Double carbs;
    private Double fat;
    private String description;

    @TableField(exist = false)
    private List<String> ingredientNames; // 包含的食材名称列表
}