::: {.list}

<% for (let index = 0; index < items.length; index++) { %> <% const item =
items[index]; %> <% const requiredIds = item.required_lesson_ids || []; %> <%
const checkpointIds = item.checkpoint_ids || []; %>

```{=html}
<article
  class="fc-catalog-card fc-portfolio-card"
  data-fc-course-card
  data-course-id="<%- item.course_id %>"
  data-course-pathway="<%- item.course_pathway %>"
  data-course-status="<%- item.course_status %>"
  data-course-total="<%- item.required_lesson_count || item.lesson_count %>"
  data-course-required-ids="<%- requiredIds.join(' ') %>"
  data-course-checkpoint-ids="<%- checkpointIds.join(' ') %>"
  data-course-project-required="<%- item.project_required ? 'true' : 'false' %>"
  data-course-keywords="<%- item.course_keywords %>"
>
  <a class="fc-catalog-card-link" href="<%- item.path %>">
    <div class="fc-catalog-card-topline">
      <span class="fc-catalog-number"><%= String(index + 1).padStart(2, "0") %></span>
      <span class="fc-catalog-stage"><%= item.course_status_label %></span>
    </div>
    <h3><%= item.title %></h3>
    <div class="fc-catalog-description"><%= item.description %></div>
    <dl class="fc-course-facts">
      <div><dt>Level</dt><dd><%= item.course_level %></dd></div>
      <div><dt>Effort</dt><dd><%= item.estimated_effort %></dd></div>
      <div><dt>Prerequisite</dt><dd><%= item.prerequisite_label %></dd></div>
    </dl>
    <div class="fc-catalog-card-footer">
      <div class="fc-card-progress" aria-hidden="true">
        <span data-fc-card-progress-bar></span>
      </div>
      <span class="fc-card-progress-value" data-fc-card-progress-value>Not started</span>
      <span class="fc-catalog-open">View course <span aria-hidden="true">→</span></span>
    </div>
  </a>
</article>
```

<% } %>

:::
