select 
    *,
    {{ train_test_split( var('test_size') ) }} as train_test_identifier


from {{ ref('fruit_user_input') }}