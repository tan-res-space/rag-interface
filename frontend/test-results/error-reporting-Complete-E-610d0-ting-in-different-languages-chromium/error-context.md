# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e5]:
    - heading "RAG Interface" [level=1] [ref=e6]
    - heading "Sign in to your account" [level=6] [ref=e7]
    - generic [ref=e8]:
      - generic [ref=e9]:
        - generic [ref=e10]:
          - text: Username
          - generic [ref=e11]: "*"
        - generic [ref=e12]:
          - textbox "Username" [active] [ref=e13]
          - group:
            - generic: Username *
      - generic [ref=e14]:
        - generic:
          - text: Password
          - generic: "*"
        - generic [ref=e15]:
          - textbox "Password" [ref=e16]
          - group:
            - generic: Password *
      - button "Sign In" [ref=e17] [cursor=pointer]
```