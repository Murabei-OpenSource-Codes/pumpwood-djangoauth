SELECT *
FROM public.row_permission__description
WHERE id IN (
	SELECT row_permission_id
	FROM public.row_permission__user_m2m
	WHERE user_id = %(user_id)s

	UNION

	SELECT row_permission.row_permission_id
	FROM public.groups__group_user_m2m AS group_user_m2m
	JOIN public.row_permission__group_m2m AS row_permission
		ON group_user_m2m.group_id = row_permission.group_id
	WHERE user_id = %(user_id)s)
