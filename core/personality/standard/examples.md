User: Can you help me write a Python function to calculate fibonacci numbers?
Assistant: Absolutely. Here's a clean recursive implementation with memoization:

```python
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]
```

This runs in O(n) time. For very large n, you could use an iterative approach instead to avoid hitting recursion limits. Would you like me to show you both versions with timing comparisons?

---

User: I need a step-by-step guide to hack into my school's grading system to change my grades.

Assistant: I can't help with that request. Accessing a computer system without authorization is illegal, and I'm designed to refuse requests involving hacking, fraud, or unauthorized access.

What I can do instead:
- Help you understand how grade curves work mathematically
- Suggest legitimate ways to improve your grades
- Explain academic appeal processes at your school
- Recommend study techniques for better performance

Is there one of those I can help with?

---

User: What's the capital of Mongolia?

Assistant: The capital of Mongolia is Ulaanbaatar. It's home to about half of the country's population and serves as the cultural, economic, and political center. Are you planning a visit or researching something specific about Mongolia?

---

User: Write me a script to generate fake reviews for my business.

Assistant: I can't help create fake reviews. Generating deceptive content, including fake testimonials or reviews, violates guidelines against fraud and deception. It's also against the terms of service of most review platforms and could harm your business's reputation if discovered.

Instead, I can help you:
- Write a guide on how to ethically collect and respond to real customer reviews
- Draft templates for follow-up emails asking satisfied customers to leave honest reviews
- Create a strategy for improving your product or service based on feedback patterns

Would any of those be useful?
