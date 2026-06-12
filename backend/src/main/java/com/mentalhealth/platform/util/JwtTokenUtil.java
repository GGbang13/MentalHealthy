package com.mentalhealth.platform.util;

import com.mentalhealth.platform.config.JwtProperties;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Component
public class JwtTokenUtil {
    private final JwtProperties jwtProperties;

    public JwtTokenUtil(JwtProperties jwtProperties) {
        this.jwtProperties = jwtProperties;
    }

    public String generateToken(Long userId, String role) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("role", role);
        Date now = new Date();
        Date expireAt = new Date(now.getTime() + jwtProperties.getExpiration());
        return Jwts.builder()
            .setClaims(claims)
            .setIssuedAt(now)
            .setExpiration(expireAt)
            .signWith(getSecretKey(), SignatureAlgorithm.HS256)
            .compact();
    }

    public boolean validateToken(String token) {
        try {
            parseClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public Long getUserId(String token) {
        return Long.valueOf(String.valueOf(parseClaims(token).get("userId")));
    }

    public String getRole(String token) {
        return String.valueOf(parseClaims(token).get("role"));
    }

    private Claims parseClaims(String token) {
        return Jwts.parserBuilder().setSigningKey(getSecretKey()).build().parseClaimsJws(token).getBody();
    }

    private SecretKey getSecretKey() {
        return Keys.hmacShaKeyFor(jwtProperties.getSecret().getBytes(StandardCharsets.UTF_8));
    }
}
