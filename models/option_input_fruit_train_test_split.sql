with shuffled_model as (
 select 
    *,
    row_number() over (order by random(42)) as shuffled_row_number
 
 from {{ ref('fruit_user_input') }}
),

length_of_shuffled_model as (
    select count(*) as num_rows
    from shuffled_model
)

select 
    *,
    case 
        when shuffled_row_number <= length_of_shuffled_model.num_rows * 0.33 then 'test'
        else 'train'
    end as train_test

from shuffled_model
join length_of_shuffled_model