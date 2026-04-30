# Contributing to comfyui-yumil-mpm

Thank you for your interest in contributing.

ご関心ありがとうございます。

This extension is licensed under MIT and welcomes community contributions.

この拡張機能は MIT ライセンスでコミュニティ貢献を歓迎しています。

---

## Pull Requests / プルリクエスト

We welcome PRs for:

- Bug fixes / バグ修正
- New ComfyUI nodes that integrate with Yumil MPM / Yumil MPM と連携する新規ノード
- Workflow examples / ワークフロー例
- Documentation improvements / ドキュメント改善

For larger changes, please **open an Issue first** to discuss the approach.

大きな変更の場合は、まず Issue で方針を相談してください。

### Workflow / 流れ

1. Fork the repo / リポをフォーク
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make changes and test locally with a real ComfyUI install
4. Push your branch: `git push origin feature/my-change`
5. Open a Pull Request describing your change

ローカルで実機の ComfyUI でテストしてから PR を出してください。

---

## Local testing / ローカルテスト

To test changes:

1. Clone the repo into your `ComfyUI/custom_nodes/` directory:
   ```sh
   cd ComfyUI/custom_nodes/
   git clone https://github.com/maigonia/comfyui-yumil-mpm.git
   ```
2. Restart ComfyUI
3. Verify the Yumil MPM nodes appear in the node menu
4. Test the integration with Yumil MPM running on `localhost:19720`

---

## Code style / コードスタイル

- Match the existing style of the codebase
- Keep node names and parameter names consistent with the existing nodes
- Comment in English for code, but README / docs can be bilingual

既存コードのスタイルに合わせてください。コード内コメントは英語、README やドキュメントは日英両対応で書いてください。

---

## Issues / Issue 報告

For bug reports and feature requests, see the issue templates available when opening a [new issue](https://github.com/maigonia/comfyui-yumil-mpm/issues/new/choose).

バグ報告・機能要望は [新規 Issue](https://github.com/maigonia/comfyui-yumil-mpm/issues/new/choose) のテンプレートをご利用ください。

---

## License / ライセンス

By contributing, you agree that your contributions will be licensed under the MIT License of this repository.

貢献いただいたコードは本リポの MIT ライセンスで公開されることに同意したものとみなします。
