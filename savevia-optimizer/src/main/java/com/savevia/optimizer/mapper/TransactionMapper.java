package com.savevia.optimizer.mapper;

import com.savevia.optimizer.entity.Transaction;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface TransactionMapper {

    int insert(Transaction transaction);

    int batchInsert(@Param("list") List<Transaction> transactions);

    int updateAnalysis(Transaction transaction);

    int resetAnalysisByUserId(@Param("userId") Long userId);

    List<Transaction> findByUserIdAndDateRange(@Param("userId") Long userId,
                                                @Param("startDate") LocalDateTime startDate,
                                                @Param("endDate") LocalDateTime endDate);

    List<Transaction> findUnanalyzedByUserId(@Param("userId") Long userId);

    List<Transaction> findRecentByUserId(@Param("userId") Long userId, @Param("limit") int limit);

    Transaction findByAccountAndFlinksId(@Param("accountId") Long accountId, @Param("flinksId") String flinksId);

    List<CategorySummary> getCategorySummary(@Param("userId") Long userId, @Param("startDate") LocalDateTime startDate);

    class CategorySummary {
        public String category;
        public java.math.BigDecimal totalAmount;
        public java.math.BigDecimal totalMissed;
    }
}
