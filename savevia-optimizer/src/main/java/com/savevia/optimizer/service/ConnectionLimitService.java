package com.savevia.optimizer.service;

import com.savevia.optimizer.entity.ConnectionHistory;
import com.savevia.optimizer.entity.UserConnectionLimit;
import com.savevia.optimizer.mapper.ConnectionLimitMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Service
public class ConnectionLimitService {

    private static final Logger logger = LoggerFactory.getLogger(ConnectionLimitService.class);
    private static final DateTimeFormatter YEAR_MONTH_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM");

    private final ConnectionLimitMapper connectionLimitMapper;

    @Value("${savevia.connection.max-per-month:5}")
    private int defaultMaxConnections;

    public ConnectionLimitService(ConnectionLimitMapper connectionLimitMapper) {
        this.connectionLimitMapper = connectionLimitMapper;
    }

    /**
     * Get current month's connection limit status for a user
     */
    public UserConnectionLimit getConnectionLimit(Long userId) {
        String currentMonth = getCurrentYearMonth();
        UserConnectionLimit limit = connectionLimitMapper.findByUserAndMonth(userId, currentMonth);

        if (limit == null) {
            // Create new record for this month
            limit = new UserConnectionLimit();
            limit.setUserId(userId);
            limit.setYearMonth(currentMonth);
            limit.setConnectionCount(0);
            limit.setMaxConnections(defaultMaxConnections);
            connectionLimitMapper.insert(limit);
            logger.info("Created new connection limit record for user {} for {}", userId, currentMonth);
        }

        return limit;
    }

    /**
     * Check if user can make a new bank connection
     */
    public boolean canConnect(Long userId) {
        UserConnectionLimit limit = getConnectionLimit(userId);
        return limit.canConnect();
    }

    /**
     * Get remaining connections for this month
     */
    public int getRemainingConnections(Long userId) {
        UserConnectionLimit limit = getConnectionLimit(userId);
        return limit.getRemainingConnections();
    }

    /**
     * Record a new bank connection and increment counter
     */
    @Transactional
    public boolean recordConnection(Long userId, String institutionName, String flinksLoginId) {
        UserConnectionLimit limit = getConnectionLimit(userId);

        if (!limit.canConnect()) {
            logger.warn("User {} has reached monthly connection limit ({}/{})",
                userId, limit.getConnectionCount(), limit.getMaxConnections());
            return false;
        }

        // Increment connection count
        limit.setConnectionCount(limit.getConnectionCount() + 1);
        connectionLimitMapper.updateConnectionCount(limit);

        // Record in history
        ConnectionHistory history = new ConnectionHistory();
        history.setUserId(userId);
        history.setInstitutionName(institutionName);
        history.setAction("CONNECT");
        history.setFlinksLoginId(flinksLoginId);
        connectionLimitMapper.insertHistory(history);

        logger.info("User {} connected to {}. Connections used: {}/{}",
            userId, institutionName, limit.getConnectionCount(), limit.getMaxConnections());

        return true;
    }

    /**
     * Record a disconnect action (doesn't affect monthly limit)
     */
    public void recordDisconnect(Long userId, String institutionName, String flinksLoginId) {
        ConnectionHistory history = new ConnectionHistory();
        history.setUserId(userId);
        history.setInstitutionName(institutionName);
        history.setAction("DISCONNECT");
        history.setFlinksLoginId(flinksLoginId);
        connectionLimitMapper.insertHistory(history);

        logger.info("User {} disconnected from {}", userId, institutionName);
    }

    /**
     * Record a refresh action (doesn't affect monthly limit)
     */
    public void recordRefresh(Long userId, String institutionName, String flinksLoginId) {
        ConnectionHistory history = new ConnectionHistory();
        history.setUserId(userId);
        history.setInstitutionName(institutionName);
        history.setAction("REFRESH");
        history.setFlinksLoginId(flinksLoginId);
        connectionLimitMapper.insertHistory(history);
    }

    private String getCurrentYearMonth() {
        return LocalDate.now().format(YEAR_MONTH_FORMAT);
    }
}
