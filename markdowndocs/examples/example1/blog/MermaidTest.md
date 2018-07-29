
# Dot Test

for more info of mermaid see

- http://knsv.github.io/mermaid/

```js
!!!mermaid("mermaid_test",width=500)
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

```js
!!!mermaid("mermaid_test2",width=500)
sequenceDiagram
    participant Alice
    participant Bob
    Alice->John: Hello John, how are you?
    loop Healthcheck
        John->John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail...
    John-->Alice: Great!
    John->Bob: How about you?
    Bob-->John: Jolly good!
```

```
!!!mermaid("mermaid_test3",width=800)
gantt
    title A Gantt Diagram

    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1  , 20d
    section Another
    Task in sec      :2014-01-12  , 12d
    anther task      : 24d
```
