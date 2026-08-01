::: {.list}

<% for (let index = 0; index < items.length; index++) { %> <% const item =
items[index]; %>

```{=html}
<article class="fc-catalog-card" data-course-path="<%- item.path %>">
  <a class="fc-catalog-card-link" href="<%- item.path %>">
    <div class="fc-catalog-card-topline">
      <span class="fc-catalog-number"><%= String(index + 1).padStart(2, "0") %></span>
      <span class="fc-catalog-stage" data-fc-card-stage>Learning path</span>
    </div>
    <h3><%= item.title %></h3>
    <div class="fc-catalog-description"><%= item.description %></div>
    <div class="fc-catalog-card-footer">
      <div class="fc-card-progress" aria-hidden="true">
        <span data-fc-card-progress-bar></span>
      </div>
      <span class="fc-card-progress-value" data-fc-card-progress-value>Not started</span>
      <span class="fc-catalog-open">Explore <span aria-hidden="true">→</span></span>
    </div>
  </a>
</article>
```

<% } %>

:::
