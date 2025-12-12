package com.savevia.optimizer.mapper;

import com.savevia.optimizer.entity.MerchantCategory;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface MerchantCategoryMapper {

    @Select("SELECT * FROM merchant_categories WHERE is_active = true ORDER BY priority DESC")
    List<MerchantCategory> findAllActive();

    @Select("SELECT * FROM merchant_categories WHERE category = #{category} AND is_active = true")
    List<MerchantCategory> findByCategory(@Param("category") String category);

    @Insert("INSERT INTO merchant_categories (merchant_pattern, category, priority) " +
            "VALUES (#{merchantPattern}, #{category}, #{priority})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(MerchantCategory merchantCategory);
}
