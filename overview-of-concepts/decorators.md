# Decorators

While the one to one mapping of node -> function implementation is powerful, it can sometimes lead to repeated code. In order to avoid this, Hamilton employs decorators to promote reuse of business logic. In this section we will go ove a few different classes of decorators with some examples. For reference on specific decorators, see [available-decorators.md](../reference/api-reference/available-decorators.md "mention"). &#x20;

In Hamilton, decorators allow the author of pipelines to modify functions as well as their role in the DAG. Decorators do one (or multiple) of the following:

**Determine whether a function should exist as a transform in the DAG.**&#x20;

`@config.when` is the primary example of this. It allows the user to determine nodes that are only present in certain DAG configurations. For instance, say that your company has different marketing spend source in different geographic regions. You might write code that looks like this:

```python
from hamilton.function_modifiers import config

@config.when(region='US')
def marketing_spend(tv_spend: pd.Series, billboard_spend: pd.Series):
    return tv_spend + billboard_spend

@config.when(region='CA')
def marketing_spend(tv_spend: pd.Series, radio_spend: pd.Series):
    return tv_spend + radio_spend
```

With the code above, the implementation of `marketing_spend` will depend on whether the DAG of transforms is compiled with the region set to the US or Canada.

#### Specify the implementation of a function, including body and inputs

The function doesn't have to specify everything about the transform. In fact, with the `@does` decorator, it can be left empty! The above can be reduced even further...

```python
import functools
import operators

from hamilton.function_modifiers import config, does

def _sum_series(**series: pd.Series) -> pd.Series:
    return functools.reduce(operators.add, series.values())

@config.when(region='US')
@does(_sum_series)
def marketing_spend(tv_spend: pd.Series, billboard_spend: pd.Series):
    pass

@config.when(region='CA')
@does(_sum_series)
def marketing_spend(tv_spend: pd.Series, radio_spend: pd.Series):
    pass
```

Note that we have no implementation for the functions! They're automagically replaced. There are other decorators that similar things. `@dynamic_transform` does something similar to the above but allows for configuration of the inputs to the function as well.

**Split the function into multiple nodes in the DAG**

In order to reduce duplicated code, hamilton has decoratos that allow a single function to output multiple nodes. These can be incredibly powerful. Take, for example, the extract\_columns decorator. In this case, let's say that we have all the source spend in a big dataframe, and want to split it out into multiple columns, so the above can read it. One might write the following:

```python
import functools
import operators

from hamilton.function_modifiers import extract_columns

def _sum_series(**series: pd.Series) -> pd.Series:
    return functools.reduce(operators.add, series.values())

@extract_columns(['tv_spend', 'radio_spend', 'billboard_spend'])
def marketing_spend_df() -> pd.DataFrame:
    return load_all_marketing_spend_from_external_source()
```

The `marketing_spend_df` function becomes three separate available datums from the pipeline. Note it actually provides a fourth, as the original node itself is added so the computation is not rerun. `@extract_columns` works specially for pandas dataframes (and we'll adding support for dask and spark shortly). In fact, it will break if you try it on a function annotated with the wrong type. The other most widely used transform is `@parametrized`.

While there are decorators that don't quite fit into the above, these should give you a sense of how and why decorators are used. For more information on available decorators, see:

{% content-ref url="../reference/api-reference/available-decorators.md" %}
[available-decorators.md](../reference/api-reference/available-decorators.md)
{% endcontent-ref %}

And for more information on writing your own decorators see:

{% content-ref url="../reference/api-extensions/custom-decorators.md" %}
[custom-decorators.md](../reference/api-extensions/custom-decorators.md)
{% endcontent-ref %}