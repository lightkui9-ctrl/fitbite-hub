package com.fitbite.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.fitbite.domain.entity.Dish;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import java.util.List;

public interface DishMapper extends BaseMapper<Dish> {

    @Select("<script>" +
            "SELECT DISTINCT d.* FROM sys_dish d " +
            "JOIN sys_dish_ingredient di ON d.id = di.dish_id " +
            "WHERE di.ingredient_id IN " +
            "<foreach item='id' collection='ingredientIds' open='(' separator=',' close=')'>" +
            "#{id}" +
            "</foreach>" +
            "</script>")
    List<Dish> selectDishesByIngredientIds(@Param("ingredientIds") List<Long> ingredientIds);

    @Select("SELECT i.name FROM sys_ingredient i " +
            "JOIN sys_dish_ingredient di ON i.id = di.ingredient_id " +
            "WHERE di.dish_id = #{dishId}")
    List<String> selectIngredientNamesByDishId(@Param("dishId") Long dishId);
}