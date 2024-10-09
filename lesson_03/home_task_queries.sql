/*
 Завдання на SQL до лекції 03.
 */


/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/
SELECT c.name,
       COUNT(f.film_id) AS count_films
FROM public.film_category f
    INNER JOIN public.category c ON f.category_id = c.category_id
GROUP BY c.name
ORDER BY count_films DESC;


/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/
SELECT a.actor_id,
       a.last_name || ' ' || a.first_name AS actor_name,
       COUNT(r.rental_id) AS count_rentals
FROM public.actor a
    JOIN public.film_actor fa ON fa.actor_id = a.actor_id
    JOIN public.inventory i ON fa.film_id = i.film_id
    JOIN public.rental r ON r.inventory_id = i.inventory_id
GROUP BY a.actor_id, actor_name
ORDER BY count_rentals DESC
LIMIT 10;


/*
3.
Вивести категорія фільмів, на яку було витрачено найбільше грошей
в прокаті
*/
SELECT c.name AS category_name,
       SUM(p.amount) AS sum_payment
FROM public.category c
    JOIN public.film_category fc ON c.category_id = fc.category_id
    JOIN public.inventory i ON fc.film_id = i.film_id
    JOIN public.rental r ON r.inventory_id = i.inventory_id
    JOIN public.payment p ON p.rental_id = r.rental_id
GROUP BY c.name
ORDER BY sum_payment DESC
LIMIT 1;


/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/
SELECT f.title
FROM public.film AS f
    LEFT JOIN public.inventory i ON f.film_id = i.film_id
WHERE i.inventory_id IS NULL;


/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/
SELECT actor_id,
       actor_name,
       count_frequency
FROM (
    -- Підзапит який виставляє акторів за рангом по кількості фільмів (у спадному порядку)
    -- а також підраховує кількість фільмів в категорії Children для кожного актора
    SELECT a.actor_id,
           a.last_name || ' ' || a.first_name AS actor_name,
           COUNT(c.category_id) AS count_frequency,
           RANK() OVER (ORDER BY COUNT(c.category_id) DESC) AS rn
    FROM actor a
       JOIN film_actor fa ON fa.actor_id = a.actor_id
       JOIN film_category fc ON fc.film_id = fa.film_id
       JOIN category c ON c.category_id = fc.category_id
    WHERE c.name = 'Children'
    GROUP BY a.actor_id, actor_name
    ) AS d
WHERE rn <= 3;