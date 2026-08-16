package com.fitbite.domain.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("sys_ingredient")
public class Ingredient {
    @TableId
    private Long id;
    private String name;
    private String category;
    private String icon;
}