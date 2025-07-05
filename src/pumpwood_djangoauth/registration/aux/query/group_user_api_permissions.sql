SELECT
  sub.route_id,
  BOOL_AND(can_delete) AS can_delete,
  BOOL_AND(can_delete_file) AS can_delete_file,
  BOOL_AND(can_delete_many) AS can_delete_many,
  BOOL_AND(can_list) AS can_list,
  BOOL_AND(can_list_without_pag) AS can_list_without_pag,
  BOOL_AND(can_retrieve) AS can_retrieve,
  BOOL_AND(can_retrieve_file) AS can_retrieve_file,
  BOOL_AND(can_run_actions) AS can_run_actions,
  BOOL_AND(can_save) AS can_save
FROM (
  -- Group permissions
  -- Use general policy to add permission to all avaiable routes
  SELECT
    route.id AS route_id,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_delete,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_delete_file,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_delete_many,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_list,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_list_without_pag,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_retrieve,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_retrieve_file,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_run_actions,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_save
  FROM public.api_permission__policy_group_m2m AS group_m2m
  JOIN public.groups__group_user_m2m AS group_user_m2m
    ON group_m2m.group_id = group_user_m2m.group_id
  JOIN public.pumpwood__route AS route
    ON 1=1
  WHERE custom_policy_id IS NULL
    AND group_user_m2m.user_id = %(user_id)s

  UNION ALL

  -- Fetch group related permissions
  SELECT
    route_id,
    api_policy.can_delete,
    api_policy.can_delete_file,
    api_policy.can_delete_many,
    api_policy.can_list,
    api_policy.can_list_without_pag,
    api_policy.can_retrieve,
    api_policy.can_retrieve_file,
    api_policy.can_run_actions,
    api_policy.can_save
  FROM public.api_permission__policy_group_m2m AS group_m2m
  JOIN public.groups__group_user_m2m AS group_user_m2m
    ON group_m2m.group_id = group_user_m2m.group_id
  JOIN public.api_permission__policy AS api_policy
    ON api_policy.id = group_m2m.custom_policy_id
  WHERE group_user_m2m.user_id = %(user_id)s

  UNION ALL

  -- User permissions
  SELECT
    route.id AS route_id,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_delete,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_delete_file,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_delete_many,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_list,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_list_without_pag,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_retrieve,
    CASE
      WHEN general_policy = 'read' THEN TRUE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_retrieve_file,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_run_actions,
    CASE
      WHEN general_policy = 'read' THEN FALSE
      WHEN general_policy = 'write' THEN TRUE
      ELSE FALSE END AS can_save
  FROM public.api_permission__policy_user_m2m AS user_m2m
  JOIN public.pumpwood__route AS route
    ON 1=1
  WHERE custom_policy_id IS NULL
    AND user_m2m.user_id = %(user_id)s

  -- Fetch user related permissions
  UNION ALL

  SELECT
    route_id,
    api_policy.can_delete,
    api_policy.can_delete_file,
    api_policy.can_delete_many,
    api_policy.can_list,
    api_policy.can_list_without_pag,
    api_policy.can_retrieve,
    api_policy.can_retrieve_file,
    api_policy.can_run_actions,
    api_policy.can_save
  FROM public.api_permission__policy_user_m2m AS user_m2m
  JOIN public.api_permission__policy AS api_policy
    ON api_policy.id = user_m2m.custom_policy_id
  WHERE user_id = %(user_id)s
) AS sub
GROUP BY sub.route_id
