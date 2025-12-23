SELECT 
    currency_pair,
    COUNT(*) as nb_jours,
    MIN(date) as date_debut,
    MAX(date) as date_fin
FROM exchange_rates 
WHERE rate_type = 'actual'
  AND currency_pair = 'MAD/EUR'
GROUP BY currency_pair;
