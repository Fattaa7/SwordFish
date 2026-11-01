import { User, Workspace, Source, Conversation, ChatTurn, AnswerItem } from '../types';

export const MOCK_USER: User = {
  id: 1,
  email: 'ahmed1999fattah@gmail.com',
  created_at: '2025-09-04T10:00:00Z',
};

export const INITIAL_MOCK_WORKSPACES: Workspace[] = [
  { id: 1, name: 'Test Workspace', owner_id: 1, created_at: '2025-09-07T09:00:00Z' },
  { id: 2, name: 'Policies', owner_id: 1, created_at: '2025-09-07T09:15:00Z' },
  { id: 3, name: 'Sensitive Documents', owner_id: 1, created_at: '2025-09-07T09:30:00Z' },
  { id: 4, name: 'Books', owner_id: 1, created_at: '2025-09-07T09:45:00Z' },
  { id: 5, name: 'Google WS', owner_id: 1, created_at: '2025-09-04T12:00:00Z' },
  { id: 6, name: 'Papers', owner_id: 1, created_at: '2025-09-04T14:20:00Z' },
  { id: 7, name: 'LAST', owner_id: 1, created_at: '2025-09-05T11:10:00Z' },
  { id: 8, name: 'algo', owner_id: 1, created_at: '2025-09-05T16:40:00Z' },
];

export const INITIAL_MOCK_SOURCES: Record<number, Source[]> = {
  1: [
    {
      id: 101,
      workspace_id: 1,
      type: 'file',
      status: 'processed',
      storage_path: '/tmp/Alchemist_2.pdf',
      mime_type: 'application/pdf',
      checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      created_at: new Date(Date.now() - 3 * 3600 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 3 * 3600 * 1000).toISOString(),
    },
  ],
  2: [
    {
      id: 102,
      workspace_id: 2,
      type: 'file',
      status: 'processed',
      storage_path: '/tmp/Enterprise_Security_Policy_2025.pdf',
      mime_type: 'application/pdf',
      created_at: new Date(Date.now() - 12 * 3600 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 12 * 3600 * 1000).toISOString(),
    },
  ],
  4: [
    {
      id: 103,
      workspace_id: 4,
      type: 'file',
      status: 'processed',
      storage_path: '/tmp/Alchemist_2.pdf',
      mime_type: 'application/pdf',
      created_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString(),
    },
  ],
};

export const INITIAL_MOCK_CONVERSATIONS: Record<number, Conversation[]> = {
  1: [
    {
      id: 201,
      title: "Santiago's Discovery of...",
      is_private: true,
      created_at: '2025-09-07T12:00:00Z',
    },
    {
      id: 202,
      title: "Santiago's Discovery o...",
      is_private: true,
      created_at: '2025-09-07T11:45:00Z',
    },
    {
      id: 203,
      title: "Santiago's Discovery ...",
      is_private: true,
      created_at: '2025-09-07T12:04:00Z',
    },
    {
      id: 204,
      title: 'New Conversation',
      is_private: true,
      created_at: '2025-09-07T10:30:00Z',
    },
    {
      id: 205,
      title: 'Cities Visited by Santia...',
      is_private: true,
      created_at: '2025-09-07T09:50:00Z',
    },
  ],
  5: [],
};

export const INITIAL_MOCK_CHAT_TURNS: Record<number, ChatTurn[]> = {
  203: [
    {
      id: 'turn-1',
      query: {
        id: 301,
        query_text: 'How does the pilgrimage parallel Santiago’s Personal Legend in the novel?',
        created_at: '2025-09-07T12:03:00Z',
      },
      answer: {
        id: 401,
        query_id: 301,
        text: "pilgrimage was a defining moment for Coelho and parallels Santiago's journey in the novel, suggesting that the discovery of one's Personal Legend is intrinsically linked to a journey of self-discovery and following omens, rather than a single physical place. Ultimately, Santiago's treasure and \"legend\" were found after a transformative journey, illustrating that realizing one's Personal Legend comes through the pursuit itself and inner awakening, not just at a specific destination [0].",
        sources: [
          {
            chunk_id: 0,
            document_id: 1,
            title: 'The Alchemist',
            page_number: 144,
            source_uri: '/files/Alchemist_2.pdf',
            excerpt:
              'Every search begins with beginner’s luck. And every search ends with the victor’s being severely tested — realizing one’s Personal Legend through the transformative journey itself.',
          },
        ],
        created_at: '2025-09-07T12:04:00Z',
      },
    },
    {
      id: 'turn-2',
      query: {
        id: 302,
        query_text: 'Where did Santiago find his legend?',
        created_at: '2025-09-07T12:04:30Z',
      },
      answer: {
        id: 402,
        query_id: 302,
        text: "Santiago finds his Personal Legend through a journey of self-discovery that is inspired by his recurring dreams and encounters with several key characters, such as Melchizedek, the king of Salem. Melchizedek explains the concept of a Personal Legend to Santiago and encourages him to pursue his dreams rather than accept his life as something controlled only by fate. Melchizedek tells Santiago, “Because you really like to travel,” affirming that Santiago's love of travel is part of his calling, and they engage in a conversation that sparks Santiago's quest for hidden treasure and meaning [8]. This sense of quest and his search for fulfillment is central to Santiago eventually realizing and pursuing his Personal Legend [0].",
        sources: [
          {
            chunk_id: 8,
            document_id: 1,
            title: 'The Alchemist',
            page_number: 25,
            source_uri: '/files/Alchemist_2.pdf',
            excerpt:
              '“It’s what you have always wanted to accomplish. Everyone, when they are young, knows what their Personal Legend is,” said Melchizedek, the King of Salem.',
          },
          {
            chunk_id: 0,
            document_id: 1,
            title: 'The Alchemist',
            page_number: 144,
            source_uri: '/files/Alchemist_2.pdf',
            excerpt:
              'Remember that wherever your heart is, there you will find your treasure. The boy dug at the roots of the sycamore tree where his dream had begun.',
          },
        ],
        created_at: '2025-09-07T12:05:00Z',
      },
    },
  ],
};

export function generateMockAnswer(queryText: string): AnswerItem {
  const lower = queryText.toLowerCase();

  if (lower.includes('melchizedek') || lower.includes('urim') || lower.includes('thummim') || lower.includes('king')) {
    return {
      id: Date.now(),
      text: "Melchizedek, the King of Salem, introduces Santiago to the concept of the Personal Legend and the Soul of the World [3]. To assist Santiago on his journey when reading omens becomes difficult, Melchizedek gives him two stones—Urim and Thummim (black for 'yes' and white for 'no')—while reminding him that it is always better to make one's own decisions [8].",
      sources: [
        {
          chunk_id: 3,
          document_id: 1,
          title: 'The Alchemist',
          page_number: 22,
          source_uri: '/files/Alchemist_2.pdf',
          excerpt: 'When you want something, all the universe conspires in helping you to achieve it.',
        },
        {
          chunk_id: 8,
          document_id: 1,
          title: 'The Alchemist',
          page_number: 25,
          source_uri: '/files/Alchemist_2.pdf',
          excerpt: 'They are called Urim and Thummim. The black signifies “yes,” and the white “no.”',
        },
      ],
      created_at: new Date().toISOString(),
    };
  }

  return {
    id: Date.now(),
    text: `Based on the indexed documents in your workspace, "${queryText}" relates directly to the overarching themes of pursuing one's Personal Legend and recognizing omens along the way [8]. Through semantic retrieval and Cohere Rerank 3.5 scoring, the top passages confirm that true transformation occurs during the journey itself before returning to the sycamore tree in Andalusia [0].`,
    sources: [
      {
        chunk_id: 8,
        document_id: 1,
        title: 'The Alchemist',
        page_number: 25,
        source_uri: '/files/Alchemist_2.pdf',
        excerpt: 'Everyone, when they are young, knows what their Personal Legend is. At that point in their lives, everything is clear and everything is possible.',
      },
      {
        chunk_id: 0,
        document_id: 1,
        title: 'The Alchemist',
        page_number: 144,
        source_uri: '/files/Alchemist_2.pdf',
        excerpt: 'The treasure was buried beneath the sycamore tree in the abandoned church where Santiago first dreamed of the pyramids.',
      },
    ],
    created_at: new Date().toISOString(),
  };
}
