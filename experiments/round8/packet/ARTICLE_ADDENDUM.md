# Proposed article section (Draft 2)

## Our recommended research architecture: The AI Computational Commons

After testing and debating this idea with several AI systems, I would recommend that researchers investigate an **AI Computational Commons**: a governed ecosystem of shared, executable capabilities that multiple AI agents and providers can discover, verify, and compose without repeatedly reading the underlying implementations.

A public commons would contain common functionality such as database access, file and stream processing, communication protocols, image transforms, queries, data structures, algorithms, and design patterns. Agents could agree on what each capability guarantees and which variants exist; they need not agree that one implementation is best for every environment. Fast, memory-efficient, cloud-native, and restricted-execution variants might satisfy the same interface under different conditions.

An application would also have **private capability domains**, protecting proprietary business logic and confidential information. Public capabilities could be visible to everyone, while organization-, project-, and agent-scoped implementations would be accessible only to authorized execution hosts. Encryption, identity checks, and execution permissions are separate protections: a signed agent should not automatically be able to decrypt or execute private code.

The key element would be a **validated binding**. The agent identifies a suitable capability, the host verifies relevant compatibility and authority, and a scoped reference is established. Later calls could use that reference without repeating a full implementation or contract in model context. The host—not the AI's confidence—would recheck revocation, policy, artifact identity, and other conditions that affect the binding.

A successful public commons could make software development increasingly cumulative. Agents would spend attention selecting safe, appropriate building blocks, and create new functionality only for the parts that genuinely differ from established patterns.

**This is a strong research recommendation, not a claim that the architecture has been proven to reduce cost or is ready to replace existing software infrastructure.** Contemporary package managers and coding agents already reuse functions without reading their source, so any proposed commons must outperform that strong baseline rather than an unrealistic all-code-regenerated scenario. The percentage of any application that can be assembled from shared capabilities remains an open measurement, not a fixed 60–80% result.

