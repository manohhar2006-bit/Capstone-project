-- ============================================================
-- Zepto Data & AI Platform
-- Module 1: Data Pipeline
-- SQL Query Collection
-- ============================================================


-- ============================================================
-- Query 1: SELECT + WHERE
-- Requirement covered:
-- SELECT and WHERE
--
-- Purpose:
-- List all books with the highest rating of 5.
-- ============================================================

SELECT
    book_id,
    title,
    rating,
    price_gbp,
    category_id
FROM books
WHERE rating = 5;


-- ============================================================
-- Query 2: ORDER BY + LIMIT
-- Requirement covered:
-- ORDER BY and LIMIT
--
-- Purpose:
-- Find the 10 most expensive books based on GBP price.
-- ============================================================

SELECT
    book_id,
    title,
    price_gbp,
    rating,
    category_id
FROM books
ORDER BY price_gbp DESC
LIMIT 10;


-- ============================================================
-- Query 3: DISTINCT
-- Requirement covered:
-- DISTINCT
--
-- Purpose:
-- List all unique book ratings present in the database.
-- ============================================================

SELECT DISTINCT
    rating
FROM books
ORDER BY rating;


-- ============================================================
-- Query 4: BETWEEN
-- Requirement covered:
-- BETWEEN
--
-- Purpose:
-- List books whose GBP price is between 20 and 40,
-- inclusive.
-- ============================================================

SELECT
    book_id,
    title,
    price_gbp,
    rating,
    category_id
FROM books
WHERE price_gbp BETWEEN 20 AND 40
ORDER BY price_gbp;


-- ============================================================
-- Query 5: IN
-- Requirement covered:
-- IN
--
-- Purpose:
-- List books belonging to the Travel or Mystery
-- categories using their category IDs.
-- ============================================================

SELECT
    book_id,
    title,
    price_gbp,
    rating,
    category_id
FROM books
WHERE category_id IN (1, 2)
ORDER BY category_id, title;


-- ============================================================
-- Query 6: JOIN
-- Requirement covered:
-- JOIN
--
-- Purpose:
-- List books together with their category names.
--
-- This query demonstrates the relationship between:
-- categories.category_id
-- and
-- books.category_id
-- ============================================================

SELECT
    b.book_id,
    b.title,
    b.price_gbp,
    b.price_inr,
    b.rating,
    b.in_stock,
    c.category_name
FROM books AS b
JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY c.category_name, b.rating DESC, b.title
LIMIT 10;