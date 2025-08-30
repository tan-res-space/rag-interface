# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e5]:
    - heading "RAG Interface" [level=1] [ref=e6]
    - heading "Sign in to your account" [level=6] [ref=e7]
    - alert [ref=e8]:
      - img [ref=e10]
      - generic [ref=e12]: Login failed. Please try again.
    - generic [ref=e13]:
      - generic [ref=e14]:
        - generic [ref=e15]:
          - text: Username
          - generic [ref=e16]: "*"
        - generic [ref=e17]:
          - textbox "Username" [ref=e18]: admin
          - group:
            - generic: Username *
      - generic [ref=e19]:
        - generic [ref=e20]:
          - text: Password
          - generic [ref=e21]: "*"
        - generic [ref=e22]:
          - textbox "Password" [ref=e23]: AdminPassword123!
          - group:
            - generic: Password *
      - button "Sign In" [ref=e24] [cursor=pointer]: Sign In
```