# 🔄 Mergify Setup Guide for Kova AI System

This repository is configured with [Mergify](https://mergify.com/) for automated pull request merging. Follow this guide to complete the setup and start using automated merging.

## 📋 Current Configuration

The `.mergify.yml` file in this repository is configured to:

1. **Automatically merge PRs** when:
   - The PR has the `ready-to-merge` label
   - CI checks pass (verify-platform job)
   - At least 1 approved review
   - The PR is not a draft
   - The base branch is `main`

2. **Automatically merge Dependabot PRs** when:
   - The PR has the `ready-to-merge` label
   - CI checks pass (verify-platform job)
   - The author is `dependabot[bot]`
   - The base branch is `main`

## 🚀 Next Steps

### 1. Install Mergify GitHub App

1. Go to https://github.com/apps/mergify
2. Click **"Install"** or **"Configure"**
3. Select your repository: `Kathrynhiggs21/Kova-ai-SYSTEM`
4. Choose **"Only select repositories"** and select this repository
5. Click **"Install & Authorize"**

### 2. Test with a Pull Request

1. **Create a test branch:**
   ```bash
   git checkout -b test-mergify-setup
   echo "# Test Mergify" >> TEST_MERGIFY.md
   git add TEST_MERGIFY.md
   git commit -m "Add test file for Mergify"
   git push origin test-mergify-setup
   ```

2. **Create a Pull Request:**
   - Go to your repository on GitHub
   - Click "Compare & pull request" for the `test-mergify-setup` branch
   - Add a clear title and description
   - Create the pull request

3. **Test the automation:**
   - Wait for CI checks to complete (should pass automatically)
   - Add the `ready-to-merge` label to the pull request
   - Get at least 1 approval from a reviewer
   - Mergify should automatically squash and merge the PR

### 3. Verify Installation

After installation, you should see:
- ✅ Mergify bot appears in your repository's "Insights > Dependency graph > Dependents" section
- ✅ Mergify comments on PRs when conditions are met or not met
- ✅ Automatic merging happens when all conditions are satisfied

## 🔧 CI/CD Integration

This repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs platform verification checks
- Validates Python syntax
- Checks Docker configuration
- Provides the `verify-platform` status check that Mergify waits for

## 📝 Using Mergify

### For Regular PRs:
1. Create your pull request as usual
2. Ensure CI passes (green checkmarks)
3. Get code review and approval
4. Add the `ready-to-merge` label
5. Mergify will automatically squash and merge

### For Dependabot PRs:
1. Dependabot creates the PR automatically
2. Review the changes if needed
3. Add the `ready-to-merge` label
4. Mergify will automatically merge once CI passes

## 🛠️ Configuration Details

The Mergify configuration uses:
- **Merge method**: Squash (creates clean commit history)
- **Strict mode**: False (allows merging without rebasing)
- **Status checks**: Waits for `verify-platform` job to pass

## 🔍 Troubleshooting

If Mergify isn't working:

1. **Check the Mergify app is installed** on your repository
2. **Verify labels** - make sure `ready-to-merge` label exists and is applied
3. **Check CI status** - ensure the `verify-platform` check is passing
4. **Review permissions** - ensure Mergify has write access to the repository
5. **Check Mergify logs** - look for Mergify comments on the PR explaining why it's not merging

## 📞 Support

- **Mergify Documentation**: https://docs.mergify.com/
- **Mergify Community**: https://github.com/mergifyio/mergify/discussions
- **Repository Issues**: Create an issue in this repository for setup-specific problems

---

**Happy automated merging! 🎉**