{% macro train_test_split(test_size = 0.25) %}
    case 
        when uniform(0::float, 1::float, random(42)) > {{ test_size }} then 'train'
        else 'test'
    end
{% endmacro %}