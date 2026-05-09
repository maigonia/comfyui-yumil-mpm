# Contributing to comfyui-yumil-mpm

Thank you for your interest in contributing.

comfyui-yumil-mpm への貢献に関心を持っていただき、ありがとうございます。

This extension is licensed under MIT and welcomes community contributions.

この拡張機能は MIT ライセンスで公開されており、コミュニティからの貢献を歓迎します。

---

## Pull Requests / プルリクエスト

We welcome pull requests for:

- Bug fixes / バグ修正
- New ComfyUI nodes that integrate with Yumil MPM / Yumil MPM と連携する新しい ComfyUI ノード
- Workflow examples / ワークフロー例
- Documentation improvements / ドキュメント改善

For larger changes, please open an issue first to discuss the approach.

大きな変更の場合は、先に Issue を開いて方針を相談してください。

## Workflow / 作業の流れ

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make changes and test locally with a real ComfyUI install.
4. Push your branch: `git push origin feature/my-change`
5. Open a pull request describing your change.

実際の ComfyUI 環境で動作確認をしてからプルリクエストを送ってください。

## Local Testing / ローカルテスト

To test changes:

1. Clone the repository into your `ComfyUI/custom_nodes/` directory:

   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/maigonia/comfyui-yumil-mpm.git
   ```

2. Restart ComfyUI.
3. Verify that the Yumil MPM nodes appear in the node menu.
4. Test the integration with Yumil MPM running locally.

## Code Style / コードスタイル

- Match the existing style of the codebase.
- Keep node names and parameter names consistent with the existing nodes.
- Write code comments in English.
- Documentation may be written in English, Japanese, or both.

既存コードのスタイルに合わせ、ノード名やパラメータ名の一貫性を保ってください。

## Issues / Issue 報告

For bug reports and feature requests, use the issue templates available when opening a [new issue](https://github.com/maigonia/comfyui-yumil-mpm/issues/new/choose).

バグ報告や機能要望には、[新しい Issue](https://github.com/maigonia/comfyui-yumil-mpm/issues/new/choose) 作成時に表示されるテンプレートをご利用ください。

## License / ライセンス

By contributing, you agree that your contributions will be licensed under the MIT License of this repository.

貢献したコードやドキュメントは、このリポジトリの MIT ライセンスで公開されることに同意したものとみなされます。
